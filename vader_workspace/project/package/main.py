class Hoge:

    def hoge(self) -> None:
        pass

    @classmethod
    def fuga(cls) -> None:
        pass


def main() -> None:
    sub_class_1 = SubClass1()  # Missing import of class
    pp(sub_class_1)
    async_function()  # Missing import of async def function
    return


if __name__ == '__main__':
    main()
