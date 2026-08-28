from risc_v.modules.br_comparator import BranchComparator


class BranchUnit:

    @staticmethod
    def evaluate(rd1: int, rd2: int, br_un: bool, funct3: int) -> bool:
        br_eq, br_lt = BranchComparator.compare(rd1, rd2, br_un)

        if funct3 == 0b000:
            return br_eq
        elif funct3 == 0b001:
            return not br_eq
        elif funct3 == 0b100:
            return br_lt
        elif funct3 == 0b101:
            return not br_lt
        elif funct3 == 0b110:
            return br_lt
        elif funct3 == 0b111:
            return not br_lt

        return False
