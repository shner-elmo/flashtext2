use flashtext2_rs::{KeywordProcessor, KeywordSpan};

#[test]
fn test_from_strings() {
    let empty_slice: &[&str] = [].as_slice();
    assert_eq!(KeywordProcessor::from(empty_slice), KeywordProcessor::new(false));

    let arrays = [
        ["hello"].as_slice(),
        ["py", "Python", "I love python!"].as_slice(),
    ];

    for slice in arrays {
        let kp_from_arr = KeywordProcessor::from(slice);

        let mut kp = KeywordProcessor::new(false);
        for word in slice {
            kp.add_keyword(word, word);
        }
        assert_eq!(kp, kp_from_arr);
    }
}


#[test]
fn test_from_tuples() {
    let empty_slice: &[&str] = [].as_slice();
    assert_eq!(KeywordProcessor::from(empty_slice), KeywordProcessor::new(false));

    let arrays = [
        [("hello", "Hello!")].as_slice(),
        [("py", "Python"), ("python", "Python"), ("py3", "Python 3.0")].as_slice(),
    ];

    for slice in arrays {
        let kp_from_arr = KeywordProcessor::from(slice);

        let mut kp = KeywordProcessor::new(false);
        for (word, clean_word) in slice {
            kp.add_keyword(word, clean_word);
        }
        assert_eq!(kp, kp_from_arr);
    }
}


#[test]
fn test_extractor() {
    struct TestCase<'a> {
        words: &'a [(&'a str, &'a str)],
        input_text: &'a str,
        case_sensitive_output: &'a[&'a str],
        case_insensitive_output: &'a[&'a str],
        span_output: &'a[&'a KeywordSpan],
        replace_keywords_output: &'a str,
    }

    // let cases = [
    //     TestCase {
    //         words: [("hello", "hello")].as_ref(),
    //         input_text: "hello world",
    //         case_sensitive_output: "",
    //         case_insensitive_output: "",
    //         span_output: "",
    //         replace_keywords_output: "",
    //     },
    // ];
    // TODO: add a few dozen cases ...

    // case-insensitive
    let mut kp = KeywordProcessor::new(false);
    kp.add_keyword("Hello", "Hello");
    assert_eq!(kp.extract_keywords("hello")[0], "Hello");

    // case-sensitive
    let mut kp = KeywordProcessor::new(true);
    kp.add_keyword("Hello", "Hello");
    assert!(kp.extract_keywords("hello").is_empty());

    let mut kp = KeywordProcessor::new(true);
    kp.add_keyword("Hello", "Hello");
    assert_eq!(kp.extract_keywords("Hello")[0], "Hello");
}
