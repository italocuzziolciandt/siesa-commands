import click
from prompter.base import ConfigAuthentication
from contrib.utilities.helpers import load_config_auth
from feature_analyzer.analyzer_service import AnalyzerService
from common.app_config import app_config_instance


def validate_comma_separated_list(ctx, param, value):
    """
    Validates that the input is a comma-separated list and returns it as a Python list.
    """
    if value:
        return [item.strip() for item in value.split(",")]
    return []


@click.command()
@click.option(
    "--config-auth",
    required=True,
    type=str,
    help="Path to the authentication configuration file.",
)
@click.option(
    "--database-tables-file-path",
    required=True,
    type=str,
    help="Path to the file containing database table definitions.",
)
@click.option(
    "--procedure-entry-point-file-name",
    required=True,
    type=str,
    help="File name (without path) of the procedure entry point.",
)
@click.option(
    "--procedures-dir-path",
    required=True,
    type=str,
    help="Path to the directory containing procedure files.",
)
@click.option(
    "--application-files-dir-path",
    required=True,
    type=str,
    help="Path to the directory containing application files.",
)
@click.option(
    "--application-files-names-to-consider",
    required=True,
    type=str,
    help="Comma-separated list of application file names to consider.",
    callback=validate_comma_separated_list,
)
@click.option(
    "--output-file-path",
    required=True,
    type=str,
    help="Path to the output file for analysis results.",
)
def main(
    config_auth: str,
    database_tables_file_path: str,
    procedure_entry_point_file_name: str,
    procedures_dir_path: str,
    application_files_dir_path: str,
    application_files_names_to_consider: list[str],
    output_file_path: str,
) -> None:
    """
    Main function to analyze database features based on provided configurations and files.

    Args:
        config_auth: Path to the authentication configuration file.
        database_tables_file_path: Path to the database tables file.
        procedure_entry_point_file_name: File name for the procedure entry point.
        procedures_dir_path: Directory path containing procedure files.
        output_file_path: Path to the output file.
    """
    app_config_instance.configure_logging()

    config = load_config_auth(config=config_auth)
    configuration = ConfigAuthentication(**config)

    # Initialize the AnalyzerService with the authentication configuration
    analyzer_service = AnalyzerService(config_auth=configuration)

    # Analyze the feature using the provided file paths and configurations
    analyzer_service.analyze_feature(
        database_tables_file_path=database_tables_file_path,
        procedure_entry_point_file_name=procedure_entry_point_file_name,
        procedures_dir_path=procedures_dir_path,
        application_files_dir_path=application_files_dir_path,
        application_files_names_to_consider=application_files_names_to_consider,
        output_file_path=output_file_path,
    )


if __name__ == "__main__":
    main()
