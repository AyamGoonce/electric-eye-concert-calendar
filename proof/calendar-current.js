(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.03e7772c26dc588e.js","sha256":"03e7772c26dc588ef88ba095387d0e4191f2b191f6e5145b0332dfd19b80f6e5","count":2477,"publishedAt":"2026-09-08T21:17:07Z","state":"calendar-state.json","stateSha256":"4fa65322f7e5d4dcfcf94ba2c840889e012b974c5d311081b6758ef554c1daa2"});
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
