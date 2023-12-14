import pytest
from ape import Contract, project


############ CONFIG FIXTURES ############

# Adjust the string based on the `asset` your strategy will use
# You may need to add the token address to `tokens` fixture.
@pytest.fixture(scope="session")
def asset(tokens):
    yield project.IERC20Interface.at(tokens["usdc"])


# Adjust the amount that should be used for testing based on `asset`.
@pytest.fixture(scope="session")
def amount(asset, user, whale):
    amount = 100 * 10 ** asset.decimals()

    asset.transfer(user, amount, sender=whale)
    yield amount


############ STANDARD FIXTURES ############


@pytest.fixture(scope="session")
def daddy(accounts):
    yield accounts["0xf89d7b9c864f589bbF53a82105107622B35EaA40"]


@pytest.fixture(scope="session")
def user(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def rewards(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def management(accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def keeper(accounts):
    yield accounts[3]


@pytest.fixture(scope="session")
def tokens():
    tokens = {
        "weth": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
        "dai": "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
        "usdc": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    }
    yield tokens


@pytest.fixture(scope="session")
def whale(accounts):
    # In order to get some funds for the token you are about to use,
    # The Balancer vault stays steady ballin on almost all tokens
    # NOTE: If `asset` is a balancer pool this may cause issues on amount checks.
    yield accounts["0xf89d7b9c864f589bbF53a82105107622B35EaA40"]


@pytest.fixture(scope="session")
def weth(tokens):
    yield project.IERC20Interface.at(tokens["weth"])


@pytest.fixture(scope="session")
def weth_amount(user, weth):
    weth_amount = 10 ** weth.decimals()
    user.transfer(weth, weth_amount)
    yield weth_amount


@pytest.fixture(scope="session")
def factory(strategy):
    yield Contract(strategy.FACTORY())


@pytest.fixture(scope="session")
def set_protocol_fee(factory):
    def set_protocol_fee(protocol_fee=0):
        owner = factory.governance()
        factory.set_protocol_fee_recipient(owner, sender=owner)
        factory.set_protocol_fee_bps(protocol_fee, sender=owner)

    yield set_protocol_fee


@pytest.fixture(scope="session")
def create_strategy(management, keeper, rewards):
    def create_strategy(asset, performanceFee=1_000):
        strategy = management.deploy(project.Strategy, asset, "yStrategy-Example")
        strategy = project.IStrategyInterface.at(strategy.address)

        strategy.setKeeper(keeper, sender=management)
        strategy.setPerformanceFeeRecipient(rewards, sender=management)
        strategy.setPerformanceFee(performanceFee, sender=management)

        return strategy

    yield create_strategy


@pytest.fixture(scope="session")
def create_oracle(management):
    def create_oracle(_management=management):
        oracle = _management.deploy(project.StrategyAprOracle)

        return oracle

    yield create_oracle


@pytest.fixture(scope="session")
def strategy(asset, create_strategy):
    strategy = create_strategy(asset)

    yield strategy


@pytest.fixture(scope="session")
def oracle(create_oracle):
    oracle = create_oracle()

    yield oracle


############ HELPER FUNCTIONS ############


@pytest.fixture(scope="session")
def deposit(strategy, asset, user, amount):
    def deposit(_strategy=strategy, _asset=asset, assets=amount, account=user):
        _asset.approve(_strategy, assets, sender=account)
        _strategy.deposit(assets, account, sender=account)

    yield deposit


@pytest.fixture(scope="session")
def RELATIVE_APPROX():
    yield 1e-5
