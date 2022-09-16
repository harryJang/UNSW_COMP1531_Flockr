from auth import auth_register

def register_3_users():
    '''Register 3 users'''
    registers = []
    u_1 = auth_register("good_email1@gmail.com", "111111", "Bob", "Ross")
    u_2 = auth_register("good_email2@hotMAIL.com", "123456", "Lob", "Moss")
    u_3 = auth_register("good_email3@outlook.com", "abc123", "Bob", "Ross")
    registers.append(u_1)
    registers.append(u_2)
    registers.append(u_3)
    return registers
