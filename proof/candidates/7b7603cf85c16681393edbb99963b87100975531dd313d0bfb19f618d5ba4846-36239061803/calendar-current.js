(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7b7603cf85c16681.js","sha256":"7b7603cf85c16681393edbb99963b87100975531dd313d0bfb19f618d5ba4846","count":2089,"publishedAt":"2026-09-26T11:35:42Z","state":"calendar-state.json","stateSha256":"a9f06bbf9f94bd19ab48cc28feb7fe2d67a1925254d4e92c5ad12f76236819de","sourceState":"calendar-source-state.json","sourceStateSha256":"c0afa5301d39f458e2d06e011a0160a535eefd13622cc9f619de2e4674715999"});
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
