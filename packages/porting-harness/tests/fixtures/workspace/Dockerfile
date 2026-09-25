# The two_number_adder fixture laid out the way porting-harness expects an
# image: the reference at /workspace/reference_implementation, the target
# language's suite under /workspace/tests.
ARG AGENT_IMAGE
FROM ${AGENT_IMAGE}
ARG SOURCE_LANGUAGE
ARG TARGET_LANGUAGE
COPY two_number_adder/source/${SOURCE_LANGUAGE} /workspace/reference_implementation
COPY two_number_adder/tests/${TARGET_LANGUAGE} /workspace/tests/${TARGET_LANGUAGE}
