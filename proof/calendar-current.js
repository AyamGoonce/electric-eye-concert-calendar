(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f81d37e4e3a20b7c.js","sha256":"f81d37e4e3a20b7c872ab249b884104c1aa568ba3f56da608634e87ef127c24c","count":2180,"publishedAt":"2026-10-05T09:47:53Z","state":"calendar-state.json","stateSha256":"5a55c2e04dd54df9b206e7684432fa653062922c46eb4ddbfc8870790541e00c","sourceState":"calendar-source-state.json","sourceStateSha256":"628b35634ccb18f3dc4274ba0a5d230df86c8281d8e943d9a810c251159a63da"});
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
