use unicode_segmentation::UnicodeSegmentation;
use std::fmt::Debug;
use std::collections::{HashSet, HashMap};


// use a tuple so its easier to unpack when iterating on the matches (and so the conversion is easier with PyO3)
// static NON_WORD_BOUNDARIES: Lazy<HashSet<char>>= Lazy::new(||
//     HashSet::from_iter("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_".chars())
// );

// pub type KeywordSpan<'a> = (&'a String, usize, usize);


#[derive(PartialEq, Debug, Default)]
struct Node {
    clean_word: Option<String>,
    children: HashMap<String, Node>,  // TODO should this be an Option or just an empty HashMap?
}


#[derive(PartialEq, Debug)]
pub struct KeywordProcessor {
    trie: Node,
    len: usize,  // the number of keywords the struct contains (not the number of nodes)
    non_word_boundaries: HashSet<char>,
    case_sensitive: bool,
}

impl KeywordProcessor {
    // TODO: use the builder pattern for configuring:
    //  - `case_sensitive`
    //  - `non_word_boundaries`
    //  - `split_text_func`
    pub fn new(case_sensitive: bool) -> Self {
        Self {
            trie: Node::default(),
            len: 0,
            non_word_boundaries: HashSet::from_iter("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_".chars()),
            case_sensitive,
        }
    }

    // TODO: should the order of the parameters be reversed?
    pub fn with_non_word_boundaries(chars: HashSet<char>, case_sensitive: bool) -> Self {
        Self {
            trie: Node::default(),
            len: 0,
            non_word_boundaries: chars,
            case_sensitive,
        }
    }

    #[inline]
    pub fn non_word_boundaries(&self) -> HashSet<char> {
        self.non_word_boundaries.clone()
    }

    #[inline]
    pub fn case_sensitive(&self) -> bool {
        self.case_sensitive
    }

    #[inline]
    pub fn len(&self) -> usize {
        self.len
    }

    #[inline]
    pub fn is_empty(&self) -> bool {
        // or `self.trie.children.is_empty()`
        self.len == 0
    }

    // we want to keep the implementation of the trie private, because it will probably change in the future
    // fn trie(&self) -> &Node {
    //     &self.trie
    // }

    #[inline]
    pub fn add_keyword(&mut self, word: &str, clean_word: &str) {
        let normalized_word = {
            if !self.case_sensitive {
                word.to_lowercase()
            } else {
                word.to_string()
            }
        };

        let mut trie = &mut self.trie;

        for word in normalized_word.split_word_bounds() {
            // TODO: remove `.to_string()`
            trie = trie.children.entry(word.to_string()).or_default();
        };

        // increment `len` only if the keyword isn't already there
        if trie.clean_word.is_none() {
            self.len += 1;
        }
        // but even if there is already a keyword, the user can still overwrite its `clean_word`
        trie.clean_word = Some(clean_word.to_string());
    }

    // pub fn add_keywords_from(&mut self, words: &[(&str, &str)]) {
    //     for (word, clean_word) in words {
    //         self.add_keyword(word, clean_word);
    //     }
    // }

    // TODO: make this a lazy-iterator
    pub fn extract_keywords(&self, text: &str) -> Vec<&String> {
        let text = {
            if !self.case_sensitive {
                text.to_lowercase()
            } else {
                text.to_string()
            }
        };

        let mut words: Vec<(usize, &str)> = text.split_word_bound_indices().collect();
        // words.push("".to_string());
        let mut keywords_found = vec![];
        let mut node = &self.trie;

        let mut idx = 0;
        let mut n_words_covered = 0;
        let mut last_keyword_found = None;

        while idx < words.len() {
            let (_, word) = words[idx];
            n_words_covered += 1;

            if let Some(child) = node.children.get(word) {
                node = child;
                if let Some(clean_word) = &node.clean_word {
                    last_keyword_found = Some(clean_word);
                }
            } else {
                // TODO: use `if let Some(val)`
                match last_keyword_found {
                    Some(keyword) => {
                        keywords_found.push(keyword);
                        last_keyword_found = None;
                        idx -= 1;
                    },
                    None => {
                        idx -= n_words_covered - 1;
                    }
                }
                node = &self.trie;
                n_words_covered = 0;
            }
            idx += 1;
        }

        if let Some(keyword) = last_keyword_found {
            keywords_found.push(keyword);
        }

        keywords_found
    }

    pub fn extract_keywords_with_span(&self, text: &str) -> Vec<(&String, usize, usize)> {
        let text = {
            if !self.case_sensitive {
                text.to_lowercase()
            } else {
                text.to_string()
            }
        };

        let mut words: Vec<(usize, &str)> = text.split_word_bound_indices().collect();

        // TODO: test if the extra first/last iteration is needed
        // words.insert(0, "".to_string());
        // words.push("".to_string());

        let mut keywords_found = vec![];
        let mut node = &self.trie;

        let mut idx = 0;
        let mut n_words_covered = 0;
        let mut last_keyword_found = None;
        let mut last_kw_found_start_idx = 0;  // default value that will always be overwritten;
        let mut last_kw_found_end_idx = 0;  // default value that will always be overwritten;

        while idx < words.len() {
            let (start_idx, word) = words[idx];
            n_words_covered += 1;

            if let Some(child) = node.children.get(word) {
                node = child;
                if let Some(clean_word) = &node.clean_word {
                    last_keyword_found = Some(clean_word);
                    last_kw_found_end_idx = start_idx + word.len();
                }
            } else {
                match last_keyword_found {
                    Some(keyword) => {
                        keywords_found.push((
                            keyword,
                            last_kw_found_start_idx,
                            last_kw_found_end_idx,
                        ));
                        last_keyword_found = None;
                        idx -= 1;
                    },
                    None => {
                        idx -= n_words_covered - 1;
                        last_kw_found_start_idx = idx + 1;
                    }
                }
                // TODO: address the spikes in the benchmark that occur when saving the span-info
                node = &self.trie;
                n_words_covered = 0;
            }
            idx += 1;
        }

        // check if there is a token that we haven't returned
        if let Some(keyword) = last_keyword_found {
            keywords_found.push((
                keyword,
                last_kw_found_start_idx,
                last_kw_found_end_idx,
            ));
        }

        keywords_found
    }

    pub fn replace_keywords(&self, text: &str) -> String {
        // the actual string returned can be bigger or smaller than `text.len()`,
        // however it will be similar, depends on the difference of: `word.len() - clean_word.len()`
        let mut string = String::with_capacity(text.len());
        let mut prev_end = 0;
        for (keyword, start, end) in self.extract_keywords_with_span(text) {
            string += &text[prev_end..start];
            string += &keyword;
            prev_end = end;
        }
        string += &text[prev_end..];  // add the last keyword

        string.shrink_to_fit();  // if `clean_word` is smaller than `word`, then `String::with_capacity` will over-allocate
        string
    }
}

impl Default for KeywordProcessor {
    fn default() -> Self {
        Self::new(false)
    }
}

impl From<&[&str]> for KeywordProcessor {
    fn from(slice: &[&str]) -> Self {
        let mut this = Self::new(false);
        for word in slice {
            this.add_keyword(word, word);
        }
        this
    }
}

impl From<&[(&str, &str)]> for KeywordProcessor {
    fn from(slice:&[(&str, &str)]) -> Self {
        let mut this = Self::new(false);
        for (word, clean_word) in slice {
            this.add_keyword(word, clean_word);
        }
        this
    }
}


// TODO: benchmark this function Vs Regex(r'([^a-zA-Z\d])')
fn split_text_idx(text: &str, non_word_boundaries: &HashSet<char>) -> Vec<(usize, usize)> {
    if text.is_empty() {
        return vec![]
    }

    let mut vec = vec![];
    let mut start_idx = 0;
    let mut add_last_char_range = false;

    for (idx, ch) in text.char_indices() {
        if add_last_char_range {
            vec.push((start_idx, idx));
            start_idx = idx;
            add_last_char_range = false
        }
        if non_word_boundaries.contains(&ch) {
        } else {
            vec.push((start_idx, idx));
            start_idx = idx;
            add_last_char_range = true;
        }
    }

    let _ = [(0, 'H'), (1, 'e'), (2, 'l'), (3, 'l'), (4, 'o'), (5, ' '), (6, 'W'), (7, 'o'), (8, 'r'), (9, 'l'), (10, 'd')];
    let _ = [(0, 5), (5, 6), (6, 11)];

    vec
}

// TODO: benchmark this function Vs Regex(r'([^a-zA-Z\d])')

// #[inline]
// fn split_text(text: &str) -> Vec<(usize, &str)> {
//     text.split_word_bound_indices().collect()
// }
//
// // old source code:
// fn split_text_v2(text: &str, non_word_boundaries: &HashSet<char>) -> Vec<String> {
//     let mut vec = vec![];
//     let mut word = String::new();
//     for ch in text.chars() {
//         if non_word_boundaries.contains(&ch) {
//             word.push(ch);
//         } else {
//             if !word.is_empty() {
//                 vec.push(word.clone());
//                 word.clear();
//             }
//             vec.push(ch.to_string());
//         }
//     }
//
//     // check if there is a word that we haven't added yet
//     if !word.is_empty() {
//         vec.push(word.clone());
//     }
//     vec
// }


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_char_indices() {
        let kp = KeywordProcessor::new(false);
        let arr: Vec<(&str, Vec<(usize, usize)>)> = vec![
            ("Hello World", vec![(0, 5), (5, 6), (6, 11)]),
            ("C# is bad ):", vec![(0, 1), (1, 2), (2, 3), (3, 5), (5, 6), (6, 9), (9, 10), (10, 11), (11, 12)]),
            ("Java is 💩.", vec![(0, 4), (4, 5), (5, 7), (7, 8), (8, 12), (12, 13)]),
        ];
        for (string, _) in &arr {
            println!("{:?}", string);
            println!("{:?}, {}", string.char_indices().collect::<Vec<_>>(), string.len());
            println!("{:?}", split_text_idx(string, &kp.non_word_boundaries));
            println!();
        }
    }
    #[test]
    fn test_regex_splitter() {
        use regex::Regex;
        let re = Regex::new(r"([^a-zA-Z0-9_])").unwrap();

        let a: Vec<&str> = re.split("fesfes").collect();
        println!("{:#?}", a);

        let a: Vec<&str> = re.split("hello ").collect();
        println!("{:#?}", a);

        let a: Vec<&str> = re.split("hello there").collect();
        println!("{:#?}", a);

        let a: Vec<&str> = re.split("sup my   g!").collect();
        // let b = "".split_inclusive(re);
        println!("{:#?}", a);

    }

    #[test]
    fn test_default() {
        let kp = KeywordProcessor {
            trie: Node::default(),
            len: 0,
            case_sensitive: false,
            non_word_boundaries: HashSet::from_iter("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_".chars()),
        };
        assert_eq!(kp, KeywordProcessor::default());
    }

    // #[test]
    // fn test_split_text() {
    //     let non_word_boundaries = KeywordProcessor::new(false).non_word_boundaries;
    //
    //     // empty string shouldn't return anything
    //     assert!(split_text("", &non_word_boundaries).is_empty());
    //
    //     let cases = [
    //         ("Hello", vec!["Hello"]),
    //         ("Hello ", vec!["Hello", " "]),
    //         ("Hello World", vec!["Hello", " ", "World"]),
    //         (" Hello World ", vec![" ", "Hello", " ", "World", " "]),
    //         ("Hannibal was born in 247 BC, death date; unknown.", vec!["Hannibal", " ", "was", " ", "born", " ", "in", " ", "247", " ", "BC", ",",  " ", "death", " ", "date", ";", " ", "unknown", "."]),
    //         // ("!!'fesf'esfes 32!!..", vec!["!", "!", "'", "fesf", "'", "esfes", " ", "32", "!", "!", ".", "."]),
    //         ("!!'fesf'esfes 32!!..", vec!["!", "!", "'", "fesf'esfes", " ", "32", "!", "!", ".", "."]),
    //         // ("   py  .  ", vec![" ", " ", " ", "py", " ", " ", ".", " ", " "]),
    //         ("   py  .  ", vec!["   ", "py", "  ", ".", "  "]),
    //     ];
    //     for (string, vec) in cases {
    //         assert_eq!(split_text(string, &non_word_boundaries), vec);
    //     }
    // }

    #[test]
    fn test_len() {
        // start at zero
        assert_eq!(KeywordProcessor::new(true).len, 0);

        //
        let mut kp = KeywordProcessor::new(true);

        kp.add_keyword("hello", "hey");
        assert_eq!(kp.len, 1);

        kp.add_keyword("hey", "hey");
        assert_eq!(kp.len, 2);

        kp.add_keyword("bye", "hey");
        assert_eq!(kp.len, 3);

        // test same word
        let mut kp = KeywordProcessor::new(true);
        kp.add_keyword("hey", "hey");
        assert_eq!(kp.len, 1);

        kp.add_keyword("hey", "hey");
        assert_eq!(kp.len, 1);

        kp.add_keyword("hey", "bye");
        assert_eq!(kp.len, 1);

        // test same word, different casing (sensitive)
        let mut kp = KeywordProcessor::new(true);
        kp.add_keyword("hey", "hey");
        assert_eq!(kp.len, 1);

        kp.add_keyword("HEY", "hey");
        assert_eq!(kp.len, 2);

        // test same word, different casing (insensitive)
        let mut kp = KeywordProcessor::new(false);
        kp.add_keyword("hey", "hey");
        assert_eq!(kp.len, 1);

        kp.add_keyword("HEY", "hey");
        assert_eq!(kp.len, 1);
    }

    #[test]
    fn test_add_keyword() {
        // empty
        let kp = KeywordProcessor::new(true);
        let trie = Node {
            clean_word: None,
            children: HashMap::new(),
        };
        assert_eq!(kp.trie, trie);

        // test few keywords
        let mut kp = KeywordProcessor::new(true);
        kp.add_keyword("hey", "Hey");
        kp.add_keyword("hello", "Hello!");
        kp.add_keyword("hello world", "Hello World");
        kp.add_keyword("C# is no good :(", "C# bad");

        let trie = Node {
            clean_word: None,
            children: HashMap::from([
                (
                    "hey".to_string(),
                    Node { clean_word: Some("Hey".to_string()), children: HashMap::new()},
                ),
                (
                    "hello".to_string(),
                    Node { clean_word: Some("Hello!".to_string()), children: HashMap::from([
                        (
                            " ".to_string(),
                            Node { clean_word: None, children: HashMap::from([
                                (
                                    "world".to_string(),
                                    Node { clean_word: Some("Hello World".to_string()), children: HashMap::new()},
                                ),
                            ])}
                        ),
                    ])},
                ),
                (
                    "C".to_string(),
                    Node { clean_word: None, children: HashMap::from([
                        (
                            "#".to_string(),
                            Node { clean_word: None, children:  HashMap::from([
                                (
                                    " ".to_string(),
                                    Node { clean_word: None, children:  HashMap::from([
                                        (
                                            "is".to_string(),
                                            Node { clean_word: None, children:  HashMap::from([
                                                (
                                                    " ".to_string(),
                                                    Node { clean_word: None, children:  HashMap::from([
                                                        (
                                                            "no".to_string(),
                                                            Node { clean_word: None, children:  HashMap::from([
                                                                (
                                                                    " ".to_string(),
                                                                    Node { clean_word: None, children:  HashMap::from([
                                                                        (
                                                                            "good".to_string(),
                                                                            Node { clean_word: None, children:  HashMap::from([
                                                                                (
                                                                                    " ".to_string(),
                                                                                    Node { clean_word: None, children:  HashMap::from([
                                                                                        (
                                                                                            ":".to_string(),
                                                                                            Node { clean_word: None, children:  HashMap::from([
                                                                                                (
                                                                                                    "(".to_string(),
                                                                                                    Node { clean_word: Some("C# bad".to_string()), children:  HashMap::new() }
                                                                                                )
                                                                                            ])},
                                                                                        ),
                                                                                    ])},
                                                                                ),
                                                                            ])},
                                                                        ),
                                                                    ])},
                                                                ),
                                                            ])},
                                                        ),
                                                    ])},
                                                ),
                                            ])},
                                        ),
                                    ])},
                                ),
                            ])},
                        ),
                    ])},
                ),
            ]),
        };
        assert_eq!(kp.trie, trie);
    }

    // #[test]
    // fn extract_keywords() {
    //     let arr = &[
    //         ("Hello", vec!["hello"]),
    //         ("Hello world", vec!["hello world"]),
    //         ("Hello world", vec!["hello world"]),
    //     ];
    //     for (string, expected_keywords) in arr.into_iter() {
    //         let mut kp = KeywordProcessor::new(false);
    //         kp.add_keyword(string, string);
    //         assert_eq!(kp.extract_keywords(string), expected_keywords)
    //
    //     }
    // }

    #[test]
    fn extract_keywords_with_span() {

    }

    #[test]
    fn replace_keywords() {

    }
}

// TODO: move these tests to a separate module (but they need to access private Structs/fields)!!
