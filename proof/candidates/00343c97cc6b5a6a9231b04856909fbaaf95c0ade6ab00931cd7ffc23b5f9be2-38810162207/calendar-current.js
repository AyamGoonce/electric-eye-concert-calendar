(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.00343c97cc6b5a6a.js","sha256":"00343c97cc6b5a6a9231b04856909fbaaf95c0ade6ab00931cd7ffc23b5f9be2","count":2147,"publishedAt":"2026-10-15T21:31:22Z","state":"calendar-state.json","stateSha256":"4dda981df3f6daac20d6110b4353a6d3d641bbe73889e407a83f33f54df125aa","sourceState":"calendar-source-state.json","sourceStateSha256":"c373573f4f7b8d858ccd9e7827ecd19511806f0a9baf69c92918bc047e765a99"});
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
