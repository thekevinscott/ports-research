from . import __all__, embed_file, write_vector


def describe_generate_embedding():
    def it_publishes_the_two_steps():
        assert __all__ == ["embed_file", "write_vector"]

    def it_binds_the_embedder():
        assert callable(embed_file)

    def it_binds_the_writer():
        assert callable(write_vector)
