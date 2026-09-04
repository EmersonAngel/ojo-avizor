// Un APK instalado de verdad (EAS Build) no corre cerca del PC, así que
// apunta directo al sitio ya desplegado — no hace falta wifi compartida ni
// túnel. Para volver a probar con `npx expo start` contra un servidor local
// mientras se desarrolla, cambiar temporalmente a la IP del PC (misma wifi)
// o a la URL de `npx localtunnel --port 8000` (datos móviles / wifi que
// aísla dispositivos).
export const URL_API = 'https://ojo-avizor.onrender.com/api-movil/';
