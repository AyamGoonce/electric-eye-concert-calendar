(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ec03d52d4836dc2c.js","sha256":"ec03d52d4836dc2c0eca7293ce1a7136e7c93c9899e9d5c66f3c16363374c9c7","count":2147,"publishedAt":"2026-11-20T13:47:51Z","state":"calendar-state.json","stateSha256":"c3224e671d128a1c7d0a33d9f9bf1dfe5178243847fae2b72b03b13efb9ee058","sourceState":"calendar-source-state.json","sourceStateSha256":"c9b79702a1888600b2d2ee84acac2189236cc4d60605ec7b3b2c1f2286def431"});
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
