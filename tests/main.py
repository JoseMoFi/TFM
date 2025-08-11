import importlib
import inspect
import pkgutil
import traceback
from pathlib import Path


def run_all_tests(tests_pkg: str = "tests") -> None:
    """
    Descubre y ejecuta todas las funciones cuyo nombre empiece por 'run_'
    en los módulos dentro del paquete tests_pkg.
    Muestra resumen final con OK/FAIL.
    """
    tests_path = Path(tests_pkg)
    if not tests_path.exists():
        print(f"[ERROR] Carpeta de tests no encontrada: {tests_path.resolve()}")
        return

    total, passed, failed = 0, 0, 0

    for _, mod_name, _ in pkgutil.iter_modules([str(tests_path)]):
        module_fullname = f"{tests_pkg}.{mod_name}"
        try:
            module = importlib.import_module(module_fullname)
        except Exception as e:
            print(f"[FAIL] No se pudo importar {module_fullname}: {e}")
            traceback.print_exc()
            failed += 1
            continue

        # Buscar funciones run_*
        for name, fn in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("run_"):
                total += 1
                print(f"→ Ejecutando {module_fullname}.{name} ...")
                try:
                    result = fn()
                    if result is True:
                        print(f"[OK] {module_fullname}.{name}")
                        passed += 1
                    else:
                        print(f"[FAIL] {module_fullname}.{name} devolvió {result!r}")
                        failed += 1
                except Exception as e:
                    print(f"[FAIL] {module_fullname}.{name} lanzó excepción: {e}")
                    traceback.print_exc()
                    failed += 1

    print("=" * 40)
    print(f"TOTAL: {total} tests | OK: {passed} | FAIL: {failed}")
    print("=" * 40)


if __name__ == "__main__":
    run_all_tests("tests")
