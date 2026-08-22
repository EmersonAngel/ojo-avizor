// Revela con un leve movimiento hacia arriba los bloques marcados con
// data-reveal a medida que entran en pantalla. La clase con-scroll-reveal
// en <html> (ver el script inline de base.html) ya filtró los casos sin
// soporte de IntersectionObserver o con "menos movimiento" pedido en el
// sistema: si no está presente, este script no hace nada y el contenido
// se ve normalmente desde el principio.
(function () {
    if (!document.documentElement.classList.contains('con-scroll-reveal')) return;
    var elementos = document.querySelectorAll('[data-reveal]');
    if (!elementos.length) return;

    var observador = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (entrada) {
            if (entrada.isIntersecting) {
                entrada.target.classList.add('en-vista');
                observador.unobserve(entrada.target);
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });

    elementos.forEach(function (el) { observador.observe(el); });
})();
