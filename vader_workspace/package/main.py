class Hoge:

    def hoge(self) -> None:
        pass

    @classmethod
    def fuga(cls) -> None:
        pass


def main() -> None:
    sub_class_1 = SubClass1()
    pp(sub_class_1)
    return


if __name__ == '__main__':
    main()
