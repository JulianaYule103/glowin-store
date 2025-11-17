/* NAVBAR GLOWIN — FUNCIONALIDAD */

// Selección de elementos
const openSearch = document.getElementById("openSearch");
const searchOverlay = document.getElementById("searchOverlay");
const navbar = document.getElementById("navbarGlowin");

let searchVisible = false;

/* ABRIR / CERRAR BARRA DE BÚSQUEDA */

if (openSearch) {
    openSearch.addEventListener("click", function () {
        searchVisible = !searchVisible;

        if (searchOverlay) {
            searchOverlay.style.display = searchVisible ? "block" : "none";
        }
    });
}

/* AGREGAR SOMBRA AL HACER SCROLL */

window.addEventListener("scroll", function () {
    if (!navbar) return;

    if (window.scrollY > 20) {
        navbar.classList.add("navbar-shadow");
    } else {
        navbar.classList.remove("navbar-shadow");
    }
});
