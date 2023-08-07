import tkinter as tk
from tkinter import filedialog
import os
import shutil
from urllib.parse import urlparse
import re
import subprocess


def remove_tildes(text):
    # Mapa de reemplazos para las tildes
    tildes_replacements = {
        'á': 'a',
        'é': 'e',
        'ó': 'o',
        'ú': 'u',
        'Á': 'A',
        'É': 'E',
        'Í': 'I',
        'Ó': 'O',
        'Ú': 'U'
    }

    # Aplicar los reemplazos
    for char, replacement in tildes_replacements.items():
        text = text.replace(char, replacement)

    return text

def generate_cucumber_methods(text):
    methods = []
    lines = text.split("\n")
    for line in lines:
        # Buscamos las palabras clave en cada línea
        match = re.search(r"\s*(Cuando|Dado|Y|Entonces)\s*(.*)", line)
        if match:
            keyword = match.group(1)
            step = match.group(2)

            # Si es una palabra clave "Y", reemplazamos por "Cuando"
            if keyword == "Y":
                keyword = "Cuando"

            # Generamos el método correspondiente
            method = f"@{keyword}(\"{step}\")\npublic void {stepToMethodName(step)}() {{\n  }}"
            methods.append(method)

    return "\n\n".join(methods)

def stepToMethodName(step):
    # Transformamos el texto en un nombre de método válido
    method_name = step.lower().replace(" ", "_")
    return method_name


def open_folder_dialog():
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder_path)

def url_to_package_name(url):
    parsed_url = urlparse(url)

    # Obtener el nombre de dominio sin "www."
    domain_parts = parsed_url.netloc.split(".")
    if domain_parts[0].lower() == "www":
        domain_parts.pop(0)

    # Invertir la lista de partes del dominio y luego unirlas con puntos
    package_name = ".".join(reversed(domain_parts))

    return package_name
    

def replace_build_gradle():
    
    # Obtener la URL original antes de invertirla
    original_url = entry_link.get()

    #Margen del generador de codigo
    selected_folder = entry_path.get()
    link_text = entry_link.get()
    contenido = text_area.get("1.0", tk.END)
    contenido = remove_tildes(contenido)
    print("Contenido del área de texto:")
    print(contenido)

    # Creacion del proyecto inicio
   
    def run_gradle_command(command, selection):
        try:
            current_dir = os.getcwd()
            os.chdir(selected_folder)
            
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,            
                executable="C:/gradle-8.2.1/bin/gradle.bat"  # Reemplaza con la ruta completa si es necesario
            )
            
            process.stdin.write(selection + "\n")
            process.stdin.flush()

            stdout, stderr = process.communicate()

            if process.returncode == 0:
                print("Ejecución exitosa:")
                print(stdout)
            else:
                print("Error en la ejecución:")
                print(stderr)
            
            os.chdir(current_dir)
            
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el comando: {e}")
            print(e.stderr)

    #Función para copiar carpetas
    def copy_folders(source_folder, destination_folder):
        try:
            # Copiar la carpeta con todas las subcarpetas y archivos
            shutil.copytree(source_folder, destination_folder)

            print(f"Carpeta {source_folder} copiada exitosamente a {destination_folder}")
        except Exception as e:
            print(f"Error al copiar la carpeta: {e}")


    def delete_folder(folder):
        try:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                print(f"Carpeta {folder} eliminada exitosamente")
            else:
                print(f"Carpeta {folder} no encontrada en el destino")
        except Exception as e:
            print(f"Error al eliminar la carpeta: {e}")

    def delete_file(file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Archivo {file_path} eliminado exitosamente")
            else:
                print(f"Archivo {file_path} no encontrado en el destino")
        except Exception as e:
            print(f"Error al eliminar el archivo: {e}")

    # Comandos de Gradle con su respectiva selección
    commands_with_selection = [
        ("gradle init --project-name myproyect --type basic --dsl groovy","2"),
        # Puedes agregar más comandos de Gradle aquí si es necesario
    ]

    for command, selection in commands_with_selection:
        run_gradle_command(command, selection)

    # Rutas originales de las carpetas a copiar
    original_folders = [
        "achivosBase\\.gradle",
        "achivosBase\\.idea",
        "achivosBase\\src",    
    ]

    # Ruta de destino para la copia
    destination_folder = selected_folder
    # Eliminar la carpeta .gradle en el destino antes de copiarla
    delete_folder(os.path.join(destination_folder, ".gradle"))
    delete_folder(os.path.join(destination_folder, ".gitattributes"))
    
    #Cambiar el archivo .gitignore INICIO
    # Eliminar el archivo .gitignore original(que no sirve) del proyecto Java
    gitignore_path = os.path.join(selected_folder, ".gitignore")
    delete_file(gitignore_path)
    # Copiar el archivo .gitignore desde archivosBase al proyecto Java
    gitignore_base_path = os.path.abspath(os.path.join("archivosBase", ".gitignore"))
    shutil.copy(gitignore_base_path, selected_folder)
    #Cambiar el archivo .gitignore FIN

    # Copiar las carpetas
    for folder in original_folders:
        folder_name = os.path.basename(folder)
        destination_path = os.path.join(destination_folder, folder_name)
        copy_folders(folder, destination_path)
    # Creacion del proyecto fin  
 
    #fin generador de codigo
    

   
    build_gradle_original_path = ""  # Variable con valor predeterminado
    if selected_folder and os.path.isdir(selected_folder):
        build_gradle_original_path = os.path.join(selected_folder, "build.gradle")
        build_gradle_base_path = os.path.abspath(os.path.join("archivosBase", "build.gradle"))
        build_serenity_base_path = os.path.abspath(os.path.join("archivosBase", "serenity.conf"))

        # Normalizar las rutas para asegurar el formato correcto de las barras diagonales
        build_gradle_original_path = os.path.normpath(build_gradle_original_path)

        try:
            # Leer el contenido del archivo build.gradle en archivoBase
            with open(build_gradle_base_path, "r") as base_file:
                base_content = base_file.read()

            # Sobrescribir el contenido del archivo original con el contenido de archivoBase
            with open(build_gradle_original_path, "w") as new_file:
                new_file.write(base_content)

            # Verificar si existe la carpeta "src/test/resources" y crearla si no existe
            resources_folder = os.path.join(selected_folder, "src", "test", "resources")
            if not os.path.exists(resources_folder):
                os.makedirs(resources_folder)

            # Crear la carpeta Features
            features_folder = os.path.join(selected_folder, "src", "test", "resources", "features")
            if not os.path.exists(features_folder):
                os.makedirs(features_folder)

            
            # Creo el archivo

            file_path = os.path.join(features_folder, "inicio.feature")

            with open(file_path, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)


            # Copiar el archivo serenity.conf desde "archivosBase" y pegarlo en "src/test/resources"
            serenity_conf_destination = os.path.join(resources_folder, "serenity.conf")
            shutil.copy(build_serenity_base_path, serenity_conf_destination)

            # Convierte el link_text en el nombre del archivo
            nombre_paquete = url_to_package_name(link_text)
            
            #Codigo para Modificar el build.gradle INICIO
            # Ruta completa del archivo build.gradle
            build_gradle_original_path = os.path.join(selected_folder, "build.gradle")

            # Leer el contenido del archivo build.gradle base en archivoBase
            build_gradle_base_path = os.path.abspath(os.path.join("archivosBase", "build.gradle"))
            with open(build_gradle_base_path, "r") as base_file:
                base_content = base_file.read()

            # Reemplazar la línea 'group' con el nombre de paquete generado dinámicamente
            modified_content = re.sub(r"^\s*group\s+'[^']+'", f"group '{nombre_paquete}'", base_content, flags=re.MULTILINE)

            # Sobrescribir el contenido del archivo original con el contenido modificado
            with open(build_gradle_original_path, "w") as new_file:
                new_file.write(modified_content)
            #Codigo para Modificar el build.gradle FIN

            # Crear la carpeta con el nombre del paquete dentro de "selected_folder/src/main/java"
            package_folder = os.path.join(selected_folder, "src", "main", "java", nombre_paquete)
            if not os.path.exists(package_folder):
                os.makedirs(package_folder)
            
            package_folder_paquete = package_folder + nombre_paquete
            print("RUTA ESTA ES: " + package_folder_paquete)


            # Crear las carpetas "models", "pageObject", "steps" y "utils" dentro de la carpeta del paquete
            models_folder = os.path.join(package_folder,  "models")
            if not os.path.exists(models_folder):
                os.makedirs(models_folder)

            page_object_folder = os.path.join(package_folder, "pageObject")
            if not os.path.exists(page_object_folder):
                os.makedirs(page_object_folder)

            steps_folder = os.path.join(package_folder,  "steps")
            if not os.path.exists(steps_folder):
                os.makedirs(steps_folder)

            utils_folder = os.path.join(package_folder, "utils")
            if not os.path.exists(utils_folder):
                os.makedirs(utils_folder)


        

            # Crear las carpetas TEST

            # Crear la carpeta con el nombre del paquete dentro de "selected_folder/src/main/java"
            package_folder_test = os.path.join(selected_folder, "src", "test", "java", nombre_paquete)
            if not os.path.exists(package_folder_test):
                os.makedirs(package_folder_test)

            # Crear las carpetas "models", "pageObject", "steps" y "utils" dentro de la carpeta del paquete
            runners_folder = os.path.join(package_folder_test, "runners")
            if not os.path.exists(runners_folder):
                os.makedirs(runners_folder)

            # Crear las carpetas "models", "pageObject", "steps" y "utils" dentro de la carpeta del paquete
            stepDefinitions_folder = os.path.join(package_folder_test, "stepDefinitions")
            if not os.path.exists(stepDefinitions_folder):
                os.makedirs(stepDefinitions_folder)

            # Crear la clase Java dentro del runner
            # Ruta completa del archivo Runner.java
            runner_file_path = os.path.join(runners_folder, "Runner.java")        

            # Texto que se pondra en el archivo de java que se creara en la carpeta 
            print("Valor de nombre_paquete:", nombre_paquete)
            java_runner_content = f"""package {nombre_paquete}.runners;


import io.cucumber.junit.CucumberOptions;
import net.serenitybdd.cucumber.CucumberWithSerenity;
import org.junit.runner.RunWith;

@RunWith(CucumberWithSerenity.class)
@CucumberOptions(
    features = "src/test/resources/features/",
    tags = "@smokeTest",
    glue = "{nombre_paquete}.stepDefinitions",
    snippets = CucumberOptions.SnippetType.CAMELCASE
)
public class Runner {{
}}
"""
            
            # Escribir el contenido en el archivo Runner.java
            with open(runner_file_path, "w") as runner_file:
                runner_file.write(java_runner_content)

            # Crear y escribir los metodos de cucumber.
            cucumber_metodos = generate_cucumber_methods(contenido) 

            print("Metodos de cucumber: ")
            print(cucumber_metodos) 

            # Creación del archivo InicioStepsDefinitions.java
            step_definitions_package = f"{nombre_paquete}.stepDefinitions"
            steps_package = f"{nombre_paquete}.steps"

            # Generar los métodos cucumber
            cucumber_methods = generate_cucumber_methods(contenido)        

            # Combinar ambos códigos
            java_steps_content = f"""package {step_definitions_package};

import io.cucumber.java.es.*;
import {steps_package}.InicioSteps;
import net.thucydides.core.annotations.Steps;

public class InicioStepsDefinitions {{
    @Steps
    InicioSteps inicioSteps;

    // Agregar la llamada al metodo abrirNavegador() dentro del primer metodo cucumber
    @Dado("que el usuario abre la pagina demo")
    public void queElUsuarioAbreLaPaginaDemo() {{
        inicioSteps.abrirNavegador();
    }}

    {cucumber_methods}    
}}
"""

            # Ruta completa del archivo InicioStepsDefinitions.java
            step_definitions_file_path = os.path.join(stepDefinitions_folder, "InicioStepsDefinitions.java")

            # Escribir el contenido en el archivo InicioStepsDefinitions.java
            with open(step_definitions_file_path, "w") as file:
                file.write(java_steps_content)


            show_message("¡Reemplazo exitoso!")
        except FileNotFoundError:
            show_message("¡Archivo build.gradle no encontrado!")
        except Exception as e:
            show_message(f"Error: {str(e)}")
            print(str(e))
    
    #Generador el achivo InicioPage.java INICIO
    def generate_inicio_page_class(package_name):
        # Ruta completa del archivo InicioPage.java
        inicio_page_file_path = os.path.join(selected_folder, "src", "main", "java", package_name, "pageObject", "InicioPage.java")

        # Texto de la clase InicioPage.java
        inicio_page_content = f"""package {package_name}.pageObject;

import net.serenitybdd.core.pages.PageObject;

public class InicioPage extends PageObject {{
    // Aqui puedes agregar los metodos y atributos especificos de la pagina de inicio
}}
"""

        # Escribir el contenido en el archivo InicioPage.java
        with open(inicio_page_file_path, "w") as inicio_page_file:
            inicio_page_file.write(inicio_page_content)
    #Generador el achivo InicioPage.java FIN

    # Generar la clase InicioPage.java con el package adecuado
    generate_inicio_page_class(nombre_paquete)

    #Generador del archivo InicioSteps INICIO
     # Crear la clase Java dentro de "steps"
    # Ruta completa del archivo InicioSteps.java
    steps_file_path = os.path.join(steps_folder, "InicioSteps.java")

    # Ajustar el nombre del paquete para el primer import
    first_import_package = ".".join(nombre_paquete.split(".")[::-1])

    # Generar el nombre del paquete para el import de InicioPage
    inicio_page_package = url_to_package_name(link_text)

    # Texto que se pondrá en el archivo Java que se creará en la carpeta "steps"
    # Texto que se pondrá en el archivo Java que se creará en la carpeta "steps"
    java_steps_content = f"""package {nombre_paquete}.steps;

import {nombre_paquete}.pageObject.InicioPage;
import net.thucydides.core.annotations.Step;
import org.fluentlenium.core.annotation.Page;

public class InicioSteps {{
    @Page
    InicioPage inicio;

    @Step("Abrir el navegador")
    public void abrirNavegador() {{
        inicio.openUrl("{original_url}");
    }}
}}
"""
    # Escribir el contenido en el archivo InicioSteps.java
    with open(steps_file_path, "w") as steps_file:
        steps_file.write(java_steps_content)
    #Generador del archivo InicioSteps FIN


def show_message(message):
    message_var.set(message)
    root.after(3000, clear_message)

def clear_message():
    message_var.set("")

# Crea la ventana principal
root = tk.Tk()
root.title("Estructura proyecto")

# Crea el Frame para la parte superior
frame_top = tk.Frame(root)
frame_top.pack(padx=10, pady=10)

# Crea el campo de texto y el botón en la parte superior
label_path = tk.Label(frame_top, text="Ruta de la carpeta:")
entry_path = tk.Entry(frame_top, width=40)
button_browse = tk.Button(frame_top, text="Buscar carpeta", command=open_folder_dialog)

# Ubica los widgets en la parte superior
label_path.grid(row=0, column=0, padx=5, pady=5)
entry_path.grid(row=0, column=1, padx=5, pady=5)
button_browse.grid(row=0, column=2, padx=5, pady=5)

# Crea el campo de texto para el link
label_link = tk.Label(frame_top, text="Link:")
entry_link = tk.Entry(frame_top, width=40)
label_link.grid(row=1, column=0, padx=5, pady=5)
entry_link.grid(row=1, column=1, padx=5, pady=5)



# Crea el Frame para la parte inferior
frame_bottom = tk.Frame(root)
frame_bottom.pack(padx=10, pady=10)

# Crea un área de texto en la parte inferior
text_area = tk.Text(frame_bottom, width=70, height=15)  # Ajusta el tamaño del área de texto
text_area.pack(padx=5, pady=5)

# Texto predeterminado para el área de texto
default_text = """#language:es 
Característica:

@smokeTest
Escenario:

Dado

Cuando

Y

Entonces

"""

# Inserta el texto predeterminado en el área de texto
text_area.insert("1.0", default_text)

# Etiqueta para mostrar mensajes de resultado
message_var = tk.StringVar()
message_label = tk.Label(root, textvariable=message_var, fg="green", font=("Arial", 12))
message_label.pack(pady=10)

# Botón para realizar el reemplazo
replace_button = tk.Button(root, text="Generar", command=replace_build_gradle)
replace_button.pack()

# Ejecuta la ventana
root.mainloop()
