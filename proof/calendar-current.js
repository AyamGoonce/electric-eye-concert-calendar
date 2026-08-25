(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9f89a05b5e9e6a73.js","sha256":"9f89a05b5e9e6a732cbbbd4565c6794c6b1cf332dbfddd460a3388b5bdef11a2","count":1732,"publishedAt":"2026-08-25T07:17:22Z","state":"calendar-state.json","stateSha256":"61df3762ecebde4a54d37bb2146bf7b35ccda118c3577c71cc03fbd003221b1a"});
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
