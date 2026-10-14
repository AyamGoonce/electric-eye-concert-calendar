(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.31b71247c783c4af.js","sha256":"31b71247c783c4af0c1e3a285ef266e37c31349e1f466e34082a0b1c94e21ec8","count":2148,"publishedAt":"2026-10-14T05:02:15Z","state":"calendar-state.json","stateSha256":"dd7eb0f32dc22902c0b0bca616b8f70e7aad94f50b813b20cebffff666b9fd9c","sourceState":"calendar-source-state.json","sourceStateSha256":"85dadf1d7d062f13bc0cd761623ce52e9679ea1a956edb7be0532835faf26e4c"});
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
