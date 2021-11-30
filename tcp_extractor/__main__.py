from cognite.extractorutils import Extractor
from dotenv import load_dotenv

from tcp_extractor import __version__
from tcp_extractor.config import Config
from tcp_extractor.extractor import run_extractor

# Import Environment Variables
load_dotenv("./tcp_extractor/.env")


def main() -> None:
    with Extractor(
        name="tcp_extractor",
        description="TCP Extractor",
        config_class=Config,
        run_handle=run_extractor,
        version=__version__,
    ) as extractor:
        extractor.run()


if __name__ == "__main__":
    main()
