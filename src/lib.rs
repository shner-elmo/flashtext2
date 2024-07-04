use flashtext2_rs;

#[cfg(not(test))]
use pyo3::prelude::*;

#[derive(Debug, PartialEq)]
enum KeywordProcessor {
    CaseSensitive(flashtext2_rs::case_sensitive::KeywordProcessor),
    CaseInsensitive(flashtext2_rs::case_insensitive::KeywordProcessor),
}

macro_rules! duplicate_body {
    ($inner:expr, $var:ident, $body:expr) => {
        match $inner {
            KeywordProcessor::CaseSensitive($var) => $body,
            KeywordProcessor::CaseInsensitive($var) => $body,
        }
    };
}

#[cfg(not(test))]
#[pyclass]
#[pyo3(module = "flashtext2", name = "KeywordProcessor")]
#[derive(PartialEq, Debug)]
struct PyKeywordProcessor {
    inner: KeywordProcessor,
}

#[cfg(not(test))]
#[pymethods]
impl PyKeywordProcessor {
    #[new]
    // #[pyo3(signature = (case_sensitive=false))]
    fn __new__(case_sensitive: bool) -> Self {
        Self {
            inner: if case_sensitive {
                KeywordProcessor::CaseSensitive(
                    flashtext2_rs::case_sensitive::KeywordProcessor::new(),
                )
            } else {
                KeywordProcessor::CaseInsensitive(
                    flashtext2_rs::case_insensitive::KeywordProcessor::new(),
                )
            },
        }
    }

    fn __len__(&self) -> usize {
        duplicate_body!(&self.inner, x, { x.len() })
    }

    fn __repr__(&self) -> String {
        "< KeywordProcessor() >".to_string()
    }

    #[getter]
    fn case_sensitive(&self) -> bool {
        matches!(self.inner, KeywordProcessor::CaseSensitive(_))
    }

    #[pyo3(signature = (word, clean_word=None))]
    fn add_keyword(&mut self, word: String, clean_word: Option<String>) {
        duplicate_body!(&mut self.inner, inner, {
            match clean_word {
                Some(clean_word) => inner.add_keyword_with_clean_word(word, clean_word),
                None => inner.add_keyword(word),
            }
        })
    }

    fn add_keywords_from_iter<'py>(&mut self, words: Bound<'py, PyAny>) {
        duplicate_body!(&mut self.inner, inner, {
            // TODO: benchmark iterating inside GIL lock, vs reaquiring on each next() call
            let iter = words
                .iter()
                .unwrap()
                .map(|py_obj| py_obj.unwrap().extract::<String>().unwrap());

            inner.add_keywords_from_iter(iter);
        })
    }

    fn add_keywords_with_clean_word_from_iter<'py>(&mut self, words: Bound<'py, PyAny>) {
        duplicate_body!(&mut self.inner, inner, {
            let iter = words
                .iter()
                .unwrap()
                .map(|py_obj| py_obj.unwrap().extract::<(String, String)>().unwrap());

            inner.add_keywords_with_clean_word_from_iter(iter);
        })
    }

    // TODO: return an iterator
    fn extract_keywords<'a>(&'a self, text: &'a str) -> Vec<&str> {
        duplicate_body!(&self.inner, inner, {
            inner.extract_keywords(text).collect()
        })
    }

    // TODO: return an iterator
    // test this: https://github.com/G-Research/ahocorasick_rs/blob/034e3f67e12198c08137bb9fb3153cb01cf5da31/src/lib.rs#L72-L87
    fn extract_keywords_with_span<'a>(&'a self, text: &'a str) -> Vec<(&str, usize, usize)> {
        duplicate_body!(&self.inner, inner, {
            if text.is_ascii() {
                inner.extract_keywords_with_span(text).collect()
            } else {
                let mut vec = vec![];
                let mut it = text.char_indices().enumerate();
                for (clean_word, mut word_start, mut word_end) in
                    inner.extract_keywords_with_span(text)
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
        })
    }

    fn replace_keywords(&self, text: &str) -> String {
        duplicate_body!(&self.inner, inner, { inner.replace_keywords(text) })
    }
}

#[cfg(not(test))]
#[pymodule]
fn flashtext2(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyKeywordProcessor>()?;
    Ok(())
}

// TODO: (flashtext-rs) fix lifetimes issues, take string by value instead of reference before cloning
// TODO: benchmark `words: Vec<str>` Vs `words: PyIterator<str>` and see if there is a difference
