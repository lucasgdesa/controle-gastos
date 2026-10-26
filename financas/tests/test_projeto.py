import subprocess
from pathlib import Path

from django.conf import settings

RAIZ = Path(settings.BASE_DIR)


def arquivos_versionados():
    saida = subprocess.run(
        ["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True, check=True
    )
    return saida.stdout.split()


def test_env_nao_e_versionado_e_exemplo_e():  # CA25
    arquivos = arquivos_versionados()
    assert ".env" not in arquivos
    assert ".env.example" in arquivos
    assert "db.sqlite3" not in arquivos


def test_secret_key_nao_esta_escrita_no_settings():  # CA25
    codigo = (RAIZ / "setup" / "settings.py").read_text(encoding="utf-8")
    assert "django-insecure" not in codigo
    assert 'os.environ["SECRET_KEY"]' in codigo
