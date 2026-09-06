(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d004552e79c01540.js","sha256":"d004552e79c015400063e88119d565a2371aa552e2a6c8ff62e6b6eee9366c18","count":2467,"publishedAt":"2026-09-06T13:27:07Z","state":"calendar-state.json","stateSha256":"2936c1a265a68e7bafc29369e8bfcbc591985d46ec895f352dac46e0e5ff2f04"});
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
