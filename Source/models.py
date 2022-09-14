# coding: utf-8
from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, Float, Date, ForeignKey, Index, Integer, Numeric, String, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Loan(Base):
    __tablename__ = 'loan'
    __table_args__ = (
        CheckConstraint("(payment_mode)::text = ANY (ARRAY[('ONLINE'::character varying)::text, ('CASH'::character varying)::text])"),
    )

    loan_id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    payment_mode = Column(String(50), nullable=False)
    interest_rate = Column(Integer, nullable=False)
    loan_period = Column(Integer, nullable=False)
    loan_date = Column(Date, nullable=False)
    loan_type = Column(String(50), nullable=False)
    authorized = Column(Boolean, nullable=False)


class HomeLoan(Loan):
    __tablename__ = 'home_loan'

    street = Column(String(50), nullable=False)
    postcode = Column(ForeignKey('postal.postcode'), nullable=False, index=True)
    loan_id = Column(ForeignKey('loan.loan_id'), primary_key=True)

    postal = relationship('Postal')


class StudentLoan(Loan):
    __tablename__ = 'student_loan'

    loan_purpose = Column(String(50), nullable=False)
    loan_id = Column(ForeignKey('loan.loan_id'), primary_key=True)


class Postal(Base):
    __tablename__ = 'postal'

    postcode = Column(Integer, primary_key=True)
    city = Column(String(50))


class Branch(Base):
    __tablename__ = 'branch'

    b_code = Column(Integer, primary_key=True)
    postcode = Column(ForeignKey('postal.postcode'), nullable=False, index=True)
    mgr_id = Column(Integer, index=True)

    postal = relationship('Postal')


class Customer(Base):
    __tablename__ = 'customer'

    postcode = Column(ForeignKey('postal.postcode'), nullable=False, unique=True)
    street = Column(String(50), nullable=False)
    c_id = Column(Integer, primary_key=True)
    f_name = Column(String(50), nullable=False)
    l_name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    b_date = Column(Date, nullable=False)
    ph_no = Column(BigInteger, nullable=False)

    postal = relationship('Postal')


class Repayment(Base):
    __tablename__ = 'repayment'

    repayment_date = Column(Date, nullable=False)
    amount = Column(Integer, nullable=False)
    loan_id = Column(ForeignKey('loan.loan_id'), primary_key=True, nullable=False)
    repayment_time = Column(Time, primary_key=True, nullable=False)

    loan = relationship('Loan')


class Account(Base):
    __tablename__ = 'account'
    __table_args__ = (
        CheckConstraint("(acc_type)::text = ANY (ARRAY[('CURRENT'::character varying)::text, ('SAVING'::character varying)::text])"),
        CheckConstraint('interest_rate = ANY (ARRAY[5.5, (6)::numeric, 6.5, (7)::numeric, 7.5, (8)::numeric, 8.5, (9)::numeric, 9.5, (10)::numeric, 10.5, (11)::numeric, 11.5, (12)::numeric])')
    )

    account_no = Column(Integer, primary_key=True, unique=True)
    balance = Column(Integer, nullable=False)
    acc_type = Column(String(50), nullable=False)
    acc_password = Column(Integer, nullable=False)
    interest_rate = Column(Numeric(2, 1), nullable=False)
    c_id = Column(ForeignKey('customer.c_id'), nullable=False)

    c = relationship('Customer')


class Current(Account):
    __tablename__ = 'current'

    min_balance = Column(Integer, nullable=False)
    account_no = Column(ForeignKey('account.account_no'), primary_key=True)


class Saving(Account):
    __tablename__ = 'savings'

    max_limit = Column(BigInteger, nullable=False)
    account_no = Column(ForeignKey('account.account_no'), primary_key=True)


class Employee(Base):
    __tablename__ = 'employee'
    __table_args__ = (
        CheckConstraint("(designation)::text = ANY (ARRAY[('PHONE OPERATOR'::character varying)::text, ('PHONE ANALYST'::character varying)::text, ('MANAGER'::character varying)::text, ('CHARTERED ACCOUNTANT'::character varying)::text, ('COUNTER AGENT'::character varying)::text, ('CHAIRMAN'::character varying)::text, ('FINANCE ANALYST'::character varying)::text])"),
    )

    e_id = Column(Integer, primary_key=True)
    f_name = Column(String(50), nullable=False)
    l_name = Column(String(50), nullable=False)
    sal = Column(Integer, nullable=False)
    password_ = Column(Integer, nullable=False)
    designation = Column(String(50), nullable=False)
    strt_date = Column(Date, nullable=False)
    email = Column(String(50), nullable=False)
    bcode = Column(ForeignKey('branch.b_code'), nullable=False)
    manages_eid = Column(ForeignKey('employee.e_id'))

    branch = relationship('Branch')
    parent = relationship('Employee', remote_side=[e_id])


class AccountOpenningRecord(Base):
    __tablename__ = 'account_openning_record'
    __table_args__ = (
        CheckConstraint("(authorization_status)::text = ANY (ARRAY[('PENDING'::character varying)::text, ('PROCESSED'::character varying)::text, ('REJECTED'::character varying)::text, ('REMOVED'::character varying)::text, ('ACCEPTED'::character varying)::text])"),
        Index('account_opening_index', 'c_id', 'account_no', 'e_id', unique=True)
    )

    c_id = Column(ForeignKey('customer.c_id'), primary_key=True, nullable=False)
    account_no = Column(ForeignKey('account.account_no'), primary_key=True, nullable=False)
    e_id = Column(ForeignKey('employee.e_id'), primary_key=True, nullable=False)
    authorization_status = Column(String(50), nullable=False)
    openning_date = Column(Date, nullable=False)

    account = relationship('Account')
    c = relationship('Customer')
    e = relationship('Employee')


class Card(Base):
    __tablename__ = 'card_'

    card_no = Column(BigInteger, primary_key=True)
    exp_date = Column(Date, nullable=False)
    issue_date = Column(Date, nullable=False)
    card_type = Column(String(50), nullable=False)
    cvv_code = Column(Integer, nullable=False)
    account_no = Column(ForeignKey('account.account_no'), nullable=False, index=True)

    account = relationship('Account')


class CustomerServiceRecord(Base):
    __tablename__ = 'customer_service_record'
    __table_args__ = (
        CheckConstraint('customer_service_rating = ANY (ARRAY[5, 4, 3, 2, 1, 0])'),
    )

    service_id = Column(Integer, primary_key=True, nullable=False, unique=True)
    customer_service_rating = Column(Integer, nullable=False)
    c_id = Column(ForeignKey('customer.c_id'), primary_key=True, nullable=False)
    e_id = Column(ForeignKey('employee.e_id'), primary_key=True, nullable=False)
    SERVICE_TIME = Column(Time, primary_key=True, nullable=False)

    c = relationship('Customer')
    e = relationship('Employee')


class CustomerServiceType(CustomerServiceRecord):
    __tablename__ = 'customer_service_types'
    __table_args__ = (
        CheckConstraint("(service_type)::text = ANY (ARRAY[('ACCOUNT MANAGER'::character varying)::text, ('LOAN MANAGEMENT'::character varying)::text, ('GENERAL INFORMATION'::character varying)::text, ('CARD RELATED'::character varying)::text, ('ACCOUNT MANAGEMENT'::character varying)::text])"),
    )

    service_id = Column(ForeignKey('customer_service_record.service_id'), primary_key=True, index=True)
    service_type = Column(String(50))


class LoanAuthorizationRecord(Base):
    __tablename__ = 'loan_authorization_record'
    __table_args__ = (
        CheckConstraint("(authorization_status)::text = ANY (ARRAY[('PENDING'::character varying)::text, ('PROCESSED'::character varying)::text, ('REJECTED'::character varying)::text])"),
    )

    c_id = Column(ForeignKey('customer.c_id'), primary_key=True, nullable=False)
    loan_id = Column(ForeignKey('loan.loan_id'), primary_key=True, nullable=False)
    e_id = Column(ForeignKey('employee.e_id'), primary_key=True, nullable=False)
    authorization_status = Column(String(50), nullable=False)

    c = relationship('Customer')
    e = relationship('Employee')
    loan = relationship('Loan')


class Transaction(Base):
    __tablename__ = 'transactions'
    __table_args__ = (
        CheckConstraint("(status_)::text = ANY (ARRAY[('ACCEPTED'::character varying)::text, ('PROCESSED'::character varying)::text, ('PENDING'::character varying)::text])"),
    )

    trans_id = Column(Integer, primary_key=True)
    trans_date = Column(Date, nullable=False)
    status_ = Column(String(50), nullable=False)
    account_no = Column(ForeignKey('account.account_no'), index=True)
    trans_time = Column(Time)
    Debit = Column(Float(53))
    Credit = Column(Float(53))
    
    account = relationship('Account')


class TransferRecord(Base):
    __tablename__ = 'transfer_record'

    account_no_receiving_funds = Column(ForeignKey('account.account_no'), nullable=False, index=True)
    trans_id = Column(ForeignKey('transactions.trans_id'), primary_key=True, nullable=False)
    account_no = Column(ForeignKey('account.account_no'), primary_key=True, nullable=False, index=True)

    account = relationship('Account', primaryjoin='TransferRecord.account_no == Account.account_no')
    account1 = relationship('Account', primaryjoin='TransferRecord.account_no_receiving_funds == Account.account_no')
    trans = relationship('Transaction')
