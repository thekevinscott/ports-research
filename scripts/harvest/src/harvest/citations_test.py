from harvest.citations import ids_in, references_section


def describe_references_section():
    def it_slices_from_the_last_references_heading():
        md = "# Intro\nbody\n## References\n- arXiv:2505.07425\n"
        assert references_section(md).strip() == "- arXiv:2505.07425"

    def it_returns_the_whole_document_when_there_is_no_heading():
        md = "no heading here"
        assert references_section(md) == md


def describe_ids_in():
    def it_extracts_new_style_ids():
        assert ids_in("## References\n- arXiv:2505.07425\n") == {"2505.07425"}

    def it_extracts_old_style_ids():
        assert ids_in("## References\n- arXiv:cs.CL/0102030\n") == {"cs.CL/0102030"}

    def it_ignores_ids_outside_the_references_section():
        md = "# Intro\narXiv:1111.11111\n## References\n- arXiv:2505.07425\n"
        assert ids_in(md) == {"2505.07425"}
