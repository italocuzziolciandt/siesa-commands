import click

from .command import Service
from prompter.base import ConfigAuthentication
from contrib.utilities.helpers import load_config_auth

@click.command()
@click.help_option("-h", "--help")
@click.option(
    "--config-auth", required=True, type=str, help="Configuração de autenticação"
)
@click.option("--scene", required=True, type=str, help="Arquivo JSON da cena")
@click.option("--output", required=True, type=str, help="Arquivo Markdown de saída")
def main(config_auth: str, scene: str, output: str) -> None:
    config = load_config_auth(config=config_auth)

    service = Service(config_authentication=ConfigAuthentication(**config))
    service.run(file_scene=scene, file_md=output)


if __name__ == "__main__":
    main()
