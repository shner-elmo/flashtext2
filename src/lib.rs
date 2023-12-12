use flashtext2_rs;

#[cfg(not(test))]
use pyo3::prelude::*;

#[cfg(not(test))]
#[pyclass]
#[derive(PartialEq, Debug)]
pub struct KeywordProcessor {
    inner: flashtext2_rs::KeywordProcessor, // here we store the actual `engine` as a Rust object
    case_sensitive: bool,                   // ignored for now (TODO use this)
}

#[cfg(not(test))]
#[pymethods]
impl KeywordProcessor {
    // TODO: check if `pub` is even necessary with PyO3
    #[new]
    #[pyo3(signature = (case_sensitive=false))]
    pub fn __new__(case_sensitive: bool) -> Self {
        Self {
            inner: flashtext2_rs::KeywordProcessor::new(),
            case_sensitive,
        }
    }

    pub fn __len__(&self) -> usize {
        self.inner.len()
    }

    pub fn __repr__(&self) -> String {
        "< KeywordProcessor() >".to_string()
    }

    #[getter]
    pub fn case_sensitive(&self) -> bool {
        self.case_sensitive
    }

    // TODO: benchmark `words: Vec<str>` Vs `words: PyIterator<str>` and see if there is a difference
    #[pyo3(signature = (word, clean_word=None))]
    pub fn add_keyword(&mut self, word: String, clean_word: Option<String>) {
        match clean_word {
            Some(clean_word) => self.inner.add_keyword_with_clean_word(word, clean_word),
            None => self.inner.add_keyword(word),
        }
    }

    // TODO: take a python iterator instead of vec
    pub fn add_keywords_from_iter(&mut self, words: Vec<&str>) {
        self.inner.add_keywords_from_iter(words);
    }

    // TODO: take a python iterator instead of vec
    pub fn add_keywords_with_clean_word_from_iter(&mut self, words: Vec<(&str, &str)>) {
        self.inner.add_keywords_with_clean_word_from_iter(words);
    }

    // TODO: return an iterator
    pub fn extract_keywords<'a>(&'a self, text: &'a str) -> Vec<&str> {
        self.inner.extract_keywords(text).collect()
    }

    // TODO: return an iterator
    pub fn extract_keywords_with_span<'a>(&'a self, text: &'a str) -> Vec<(&str, usize, usize)> {
        if text.is_ascii() {
            self.inner.extract_keywords_with_span(text).collect()
        } else {
            // TODO: adjust spans by iterating on `text.char_indices().enumerate()`
            panic!("Not yet implemented for non-ascii strings")
        }
    }

    pub fn replace_keywords(&self, text: &str) -> String {
        self.inner.replace_keywords(text)
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
// 2. `split_text() -> Vec<String>` -> `split_text() -> Vec<(i32, i32)>`
// 3. split_text() {re.split_inclusive(r'([a-z...])')}
// 4. extract_keywords() -> Vec<String> Vs extract_keywords() -> { LazyExtractor {...} }

// TODO: create .pyi file
