from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


class ChainBuilder:
    def __init__(self, llm):
        self.llm = llm

    def build(self, prompt_template: str, input_vars: list[str], model):
        parser = PydanticOutputParser(pydantic_object=model)

        prompt = PromptTemplate(
            template=prompt_template + "\n\n{format_instructions}",
            input_variables=input_vars,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        return prompt | self.llm | parser
