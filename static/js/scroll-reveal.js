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

    // Un bloque que ya está visible al cargar la página (sin necesidad de
    // scroll, por ejemplo en una pantalla alta) se revela directo, sin
    // pasar por el observador: de por sí el observador debería avisar de
    // inmediato en ese caso (su primer llamado siempre reporta el estado
    // actual), pero se confirma acá aparte para no depender de eso — así
    // nunca se queda pegado invisible sin que medie ningún scroll real.
    elementos.forEach(function (el) {
        var recuadro = el.getBoundingClientRect();
        var yaVisible = recuadro.top < window.innerHeight && recuadro.bottom > 0;
        if (yaVisible) {
            el.classList.add('en-vista');
        } else {
            observador.observe(el);
        }
    });
})();
