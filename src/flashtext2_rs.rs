use std::fmt::Debug;
use std::collections::{HashSet, HashMap};


// use a tuple so its easier to unpack when iterating on the matches (and so the conversion is easier with PyO3)
// static NON_WORD_BOUNDARIES: Lazy<HashSet<char>>= Lazy::new(||
//     HashSet::from_iter("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_".chars())
// );


#[derive(PartialEq, Debug, Default)]
struct Node {
    clean_word: Option<String>,
    children: HashMap<char, Node>,  // TODO should this be an Option or just an empty HashMap?
}


#[derive(PartialEq, Debug)]
pub struct KeywordProcessor {
    trie: Node,
    len: usize,  // the number of keywords the struct contains (not the number of nodes)
    non_word_boundaries: HashSet<char>,
    case_sensitive: bool,
    max_keyword_length: usize,  // not `str.len()`, but `str.chars().count()`
}

impl KeywordProcessor {
    pub fn new(case_sensitive: bool) -> Self {
        Self {
            trie: Node::default(),
            len: 0,
            non_word_boundaries: HashSet::from_iter("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_".chars()),
            case_sensitive,
            max_keyword_length: 0,
        }
    }

    // TODO: should the order of the parameters be reversed?
    pub fn with_non_word_boundaries(chars: HashSet<char>, case_sensitive: bool) -> Self {
        Self {
            trie: Node::default(),
            len: 0,
            non_word_boundaries: chars,
            case_sensitive,
            max_keyword_length: 0,
        }
    }

    pub fn non_word_boundaries(&self) -> HashSet<char> {
        self.non_word_boundaries.clone()
    }

    pub fn case_sensitive(&self) -> bool {
        self.case_sensitive
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        // or `self.trie.children.is_empty()`
        self.len == 0
    }

    // we want to keep the implementation of the trie private, because it will probably change in the future
    // fn trie(&self) -> &Node {
    //     &self.trie
    // }

    pub fn add_keyword(&mut self, word: &str, clean_word: &str) {
        let normalized_word = {
            if !self.case_sensitive {
                word.to_lowercase()
            } else {
                word.to_string()
            }
        };

        let mut trie = &mut self.trie;
        let mut n_chars = 0;

        for ch in normalized_word.chars() {
            trie = trie.children.entry(ch).or_default();
            n_chars += 1;
        };
        self.max_keyword_length = n_chars;

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
    pub fn extract_keywords(&self, text: &str) -> Vec<(&String, usize, usize)> {
        let text = if !self.case_sensitive {
            text.to_lowercase()
        } else {
            text.to_string()
        };

        let chars: Vec<(char, bool)> = text
            .chars()
            .map(|ch| (ch, self.non_word_boundaries.contains(&ch)))
            .collect();

        let mut node = &self.trie;
        let mut keywords_found = vec![];
        let mut last_keyword_found = None;
        let mut currently_inside_word = false;

        let n_chars = chars.len();
        let mut idx = 0;
        let mut n_chars_covered = 0;

        while idx < n_chars {
            let (ch, is_non_word_boundary) = chars[idx];
            n_chars_covered += 1;

            // TODO: is `idx == 0` necessary?
            // TODO: replace `node.children.contains_key(&ch)` with `node.children.get(&ch)`
            if node.children.contains_key(&ch) && (currently_inside_word || ((idx == 0 || !chars[idx - 1].1) && is_non_word_boundary)) {
                if !currently_inside_word {
                    currently_inside_word = true;
                }
                node = &node.children[&ch];

                if let Some(ref clean_word) = &node.clean_word {
                    if is_non_word_boundary && (idx + 1 == n_chars || !chars[idx + 1].1) {
                        last_keyword_found = Some((clean_word, idx - (n_chars_covered - 1), idx));
                    }
                }
            } else {
                if let Some(keyword_found) = last_keyword_found {
                    keywords_found.push(keyword_found);
                    last_keyword_found = None;
                    idx -= 1;
                } else {
                    idx -= n_chars_covered - 1;
                }
                node = &self.trie;
                n_chars_covered = 0;
                currently_inside_word = false;
            }
            idx += 1;
        }

        // add the last keyword (if there is one)
        if let Some(keyword_found) = last_keyword_found {
            keywords_found.push(keyword_found);
        }
        keywords_found
    }

    pub fn extract_keywords_with_span(&self, text: &str) -> Vec<(&String, usize, usize)> {
        self.extract_keywords(text)
    }

    pub fn replace_keywords(&self, text: &str) -> String {
        let mut string = String::with_capacity(text.len());
        let mut prev_end = 0;
        for (keyword, start, end) in self.extract_keywords_with_span(text) {
            string += &text[prev_end..start];
            string += &keyword;
            prev_end = end;
        }
        string += &text[prev_end..];
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test() {
        let mut kp = KeywordProcessor::new(false);
        kp.add_keyword("hello", "Hello");
        println!("{:?}", kp.trie);

        println!("{:?}, {:?}", kp.extract_keywords("distributed super distributed super computing insti r"), vec!["Distributed Super Computing", "R"]);
        println!("{:?}, {:?}", kp.extract_keywords_with_span("distributed super distributed super computing insti r"), vec!["Distributed Super Computing", "R"]);
        println!("{:?}, {:?}", kp.extract_keywords("hello"), vec!["Hello"]);
        println!("{:?}, {:?}", kp.extract_keywords(" hello "), vec!["Hello"]);
        println!("{:?}, {:?}", kp.extract_keywords(" hello"), vec!["Hello"]);
        println!("{:?}, {:?}", kp.extract_keywords("  hello   "), vec!["Hello"]);
        println!("{:?}, {:?}", kp.extract_keywords("                                  hello   "), vec!["Hello"]);
        println!("{:?}, {:?}", kp.extract_keywords("hello "), vec!["Hello"]);
        println!("{:?}, {:?}", kp.extract_keywords("ahello"), Vec::<&str>::new());
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
            max_keyword_length: 0,
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
    //         ("!!'fesf'esfes 32!!..", vec!["!", "!", "'", "fesf", "'", "esfes", " ", "32", "!", "!", ".", "."]),
    //         ("   py  .  ", vec![" ", " ", " ", "py", " ", " ", ".", " ", " "]),
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
        println!("{:#?}", kp.trie);

        kp.add_keyword("hello", "Hello!");
        println!("{:#?}", kp.trie);

        kp.add_keyword("hello world", "Hello World");
        println!("{:#?}", kp.trie);

        kp.add_keyword("C# is no good :(", "C# bad");
        println!("{:#?}", kp.trie);

        // let trie = Node {
        //     clean_word: None,
        //     children: HashMap::from([
        //         (
        //             "hey".to_string(),
        //             Node { clean_word: Some("Hey".to_string()), children: HashMap::new()},
        //         ),
        //         (
        //             "hello".to_string(),
        //             Node { clean_word: Some("Hello!".to_string()), children: HashMap::from([
        //                 (
        //                     " ".to_string(),
        //                     Node { clean_word: None, children: HashMap::from([
        //                         (
        //                             "world".to_string(),
        //                             Node { clean_word: Some("Hello World".to_string()), children: HashMap::new()},
        //                         ),
        //                     ])}
        //                 ),
        //             ])},
        //         ),
        //         (
        //             "C".to_string(),
        //             Node { clean_word: None, children: HashMap::from([
        //                 (
        //                     "#".to_string(),
        //                     Node { clean_word: None, children:  HashMap::from([
        //                         (
        //                             " ".to_string(),
        //                             Node { clean_word: None, children:  HashMap::from([
        //                                 (
        //                                     "is".to_string(),
        //                                     Node { clean_word: None, children:  HashMap::from([
        //                                         (
        //                                             " ".to_string(),
        //                                             Node { clean_word: None, children:  HashMap::from([
        //                                                 (
        //                                                     "no".to_string(),
        //                                                     Node { clean_word: None, children:  HashMap::from([
        //                                                         (
        //                                                             " ".to_string(),
        //                                                             Node { clean_word: None, children:  HashMap::from([
        //                                                                 (
        //                                                                     "good".to_string(),
        //                                                                     Node { clean_word: None, children:  HashMap::from([
        //                                                                         (
        //                                                                             " ".to_string(),
        //                                                                             Node { clean_word: None, children:  HashMap::from([
        //                                                                                 (
        //                                                                                     ":".to_string(),
        //                                                                                     Node { clean_word: None, children:  HashMap::from([
        //                                                                                         (
        //                                                                                             "(".to_string(),
        //                                                                                             Node { clean_word: Some("C# bad".to_string()), children:  HashMap::new() }
        //                                                                                         )
        //                                                                                     ])},
        //                                                                                 ),
        //                                                                             ])},
        //                                                                         ),
        //                                                                     ])},
        //                                                                 ),
        //                                                             ])},
        //                                                         ),
        //                                                     ])},
        //                                                 ),
        //                                             ])},
        //                                         ),
        //                                     ])},
        //                                 ),
        //                             ])},
        //                         ),
        //                     ])},
        //                 ),
        //             ])},
        //         ),
        //     ]),
        // };
        // assert_eq!(kp.trie, trie);
    }
}

// TODO: move these tests to a separate module (but they need to access private Structs/fields)!!
