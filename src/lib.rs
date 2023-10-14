mod flashtext2_rs;

use std::collections::{HashSet};

#[cfg(not(test))]
use pyo3::prelude::*;


#[cfg(not(test))]
#[pyclass]
#[derive(PartialEq, Debug)]
pub struct KeywordProcessor {
    kp: flashtext2_rs::KeywordProcessor,  // here we store the actual `engine` as a Rust object
}

#[cfg(not(test))]
#[pymethods]
impl KeywordProcessor {

    // TODO: check if `pub` is even necessary with PyO3
    #[new]
    #[pyo3(signature = (case_sensitive=false, non_word_boundaries=None))]
    pub fn __new__(case_sensitive: bool, non_word_boundaries: Option<HashSet<char>>) -> Self {
        Self {
            kp: {
                if let Some(chars) = non_word_boundaries {
                    flashtext2_rs::KeywordProcessor::with_non_word_boundaries(chars.clone(), case_sensitive)
                } else {
                    flashtext2_rs::KeywordProcessor::new(case_sensitive)
                }
            },
        }
    }

    pub fn __len__(&self) -> usize {
        self.kp.len()
    }

    pub fn __repr__(&self) -> String {
        "< KeywordProcessor() >".to_string()
    }

    #[getter]
    pub fn case_sensitive(&self) -> bool {
        self.kp.case_sensitive()  // TODO: add this getter
    }

    #[getter]
    pub fn non_word_boundaries(&self) -> HashSet<char> {
        self.kp.non_word_boundaries()
    }

    // TODO: benchmark `words: Vec<str>` Vs `words: PyIterator<str>` and see if there is a difference
    pub fn add_keywords(&mut self, words: Vec<&str>) {
        for word in words {
            self.kp.add_keyword(word, word);
        }
    }

    pub fn add_keywords_with_clean_word(&mut self, words: Vec<(&str, &str)>) {
        for (word, clean_word) in words {
            self.kp.add_keyword(word, clean_word);
        }
    }

    // TODO: make this a lazy-iterator
    pub fn extract_keywords(&self, text: &str) -> Vec<&String> {
        self.kp.extract_keywords(text)
            .into_iter()
            .map(|(kw, _, _)| kw)
            .collect()
    }

    pub fn extract_keywords_with_span(&self, text: &str) -> Vec<(&String, usize, usize)> {
        self.kp.extract_keywords_with_span(text)
    }

    pub fn replace_keywords(&self, text: &str) -> String {
        self.kp.replace_keywords(text)
    }
}


#[cfg(not(test))]
#[pymodule]
fn flashtext2(_py: Python, m: &PyModule) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(extract_keywords, m)?)?;
    m.add_class::<KeywordProcessor>()?;
    Ok(())
}


// compare benchmarks of:
// 1. let Some(var) = val Vs var.is_some()
// 2. `split_text() -> Vec<String>` -> `split_text() -> Vec<(i32, i32)>`
// 3. split_text() {re.split_inclusive(r'([a-z...])')}
// 4. extract_keywords() -> Vec<String> Vs extract_keywords() -> { LazyExtractor {...} }
