(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4fbe45e92440e190.js","sha256":"4fbe45e92440e19066faa2327fbc990232ae08667cee4cbff27e6a9db314f584","count":2145,"publishedAt":"2026-11-19T16:58:33Z","state":"calendar-state.json","stateSha256":"8f6e9b20bac4c229f3ee25675a5fedca5cea1755148b2aff193de48c6719165e","sourceState":"calendar-source-state.json","sourceStateSha256":"1281b8b05338f24c108c70db61000a19faafc87777bcfdf55f96eb47d41e7053"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
