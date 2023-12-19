use flashtext2_rs::KeywordProcessor;

#[cfg(not(test))]
use pyo3::prelude::*;
use pyo3::types::PyIterator;

fn python_iterable_to_iterator(maybe_iterable: &PyAny) -> &PyIterator {
    maybe_iterable
        .call_method0("__iter__")
        .unwrap()
        .downcast::<PyIterator>()
        .unwrap()
}

#[cfg(not(test))]
#[pyclass]
#[pyo3(module = "flashtext2", name = "KeywordProcessor")]
#[derive(PartialEq, Debug)]
struct PyKeywordProcessor {
    inner: KeywordProcessor, // here we store the actual `engine` as a Rust object
    case_sensitive: bool,    // ignored for now (TODO use this)
}

#[cfg(not(test))]
#[pymethods]
impl PyKeywordProcessor {
    #[new]
    // #[pyo3(signature = (case_sensitive=false))]
    fn __new__(case_sensitive: bool) -> Self {
        if !case_sensitive {
            panic!("case-insensitive is not currently supported");
        }
        Self {
            inner: KeywordProcessor::new(),
            case_sensitive,
        }
    }

    fn __len__(&self) -> usize {
        self.inner.len()
    }

    fn __repr__(&self) -> String {
        "< KeywordProcessor() >".to_string()
    }

    #[getter]
    fn case_sensitive(&self) -> bool {
        self.case_sensitive
    }

    #[pyo3(signature = (word, clean_word=None))]
    fn add_keyword(&mut self, word: String, clean_word: Option<String>) {
        match clean_word {
            Some(clean_word) => self.inner.add_keyword_with_clean_word(word, clean_word),
            None => self.inner.add_keyword(word),
        }
    }

    fn add_keywords_from_iter(&mut self, words: &PyAny) {
        let iter = python_iterable_to_iterator(words)
            .iter()
            .unwrap()
            .map(|py_obj| py_obj.unwrap().extract::<&str>().unwrap());

        self.inner.add_keywords_from_iter(iter);
    }

    fn add_keywords_with_clean_word_from_iter(&mut self, words: &PyAny) {
        let iter = python_iterable_to_iterator(words)
            .iter()
            .unwrap()
            .map(|py_obj| py_obj.unwrap().extract::<(&str, &str)>().unwrap());

        self.inner.add_keywords_with_clean_word_from_iter(iter);
    }

    // TODO: return an iterator
    fn extract_keywords<'a>(&'a self, text: &'a str) -> Vec<&str> {
        self.inner.extract_keywords(text).collect()
    }

    // TODO: return an iterator
    fn extract_keywords_with_span<'a>(&'a self, text: &'a str) -> Vec<(&str, usize, usize)> {
        if text.is_ascii() {
            self.inner.extract_keywords_with_span(text).collect()
        } else {
            let mut vec = vec![];
            let mut it = text.char_indices().enumerate();
            for (clean_word, mut word_start, mut word_end) in
                self.inner.extract_keywords_with_span(text)
            {
                for (idx, (char_idx, _)) in it.by_ref() {
                    if char_idx == word_start {
                        word_start = idx;
                        break;
                    }
                }
                {
                    let old_word_end = word_end;
                    let mut last_idx = 0;
                    for (idx, (char_idx, _)) in it.by_ref() {
                        last_idx = idx;
                        if word_end == char_idx {
                            word_end = idx;
                            break;
                        }
                    }
                    if word_end == old_word_end {
                        word_end = last_idx + 1;
                    }
                }
                vec.push((clean_word, word_start, word_end));
            }
            vec
        }
    }

    fn replace_keywords(&self, text: &str) -> String {
        self.inner.replace_keywords(text)
    }
}

#[cfg(not(test))]
#[pymodule]
fn flashtext2(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyKeywordProcessor>()?;
    Ok(())
}

// TODO: create .pyi file
// TODO: (flashtext-rs) fix lifetimes issues, take string by value instead of reference before cloning
// TODO: benchmark `words: Vec<str>` Vs `words: PyIterator<str>` and see if there is a difference
