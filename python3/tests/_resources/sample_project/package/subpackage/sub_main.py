

def sub_top_level_function1(
    hoge: int,
    fuga: str,
) -> None:
    """ Top level function.

    signature is multilined.
    """
    return


class SubTopLevelClass1:

    class InnerClass1:
        """ This class should be ignored in `importing` context
        """

        def inner_instance_method1(self) -> None:
            """
            """
            return

    def instance_method1(
        self, hoge: int,
    ) -> None:
        """ Instance method.

        signature is multilined.
        """
        return


class SubTopLevelClass2:
    """
    Multiline docstring top level class.

    This should be captured.
    """
    pass
