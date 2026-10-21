(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.070eadd7d5a2ef9a.js","sha256":"070eadd7d5a2ef9a9281eb8e2d4c18e34316166cadbfe02d9861715103c526fb","count":2067,"publishedAt":"2026-10-21T21:49:45Z","state":"calendar-state.json","stateSha256":"966ea980d4850cad0b523847503692801cfb93ba71180f7f8945367f62f803e2","sourceState":"calendar-source-state.json","sourceStateSha256":"050139e12ce26fa148b44836ee4ea6047fae2feff1cc76cfdc4575b93f3eba98"});
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
