(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2b55792e27d72650.js","sha256":"2b55792e27d72650c72ca05421dee28cca4200aaebf6ab5098de2d6e0e765624","count":2210,"publishedAt":"2026-10-08T10:44:52Z","state":"calendar-state.json","stateSha256":"80ec3bdedc50d969d60742dac7c8211bd583082b32ab238ec99f1cbd092fe3a1","sourceState":"calendar-source-state.json","sourceStateSha256":"0d8000cb2dec95c64f8028922a1630700696019243a915e9d279d7e69cb3bb3e"});
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
