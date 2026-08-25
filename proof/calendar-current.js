(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1e113c2bc0480a77.js","sha256":"1e113c2bc0480a7727a1c139f0f556a277218aad3e52d01e5327391a35a133a7","count":1731,"publishedAt":"2026-08-25T09:12:05Z","state":"calendar-state.json","stateSha256":"9476cea025d8c9b161c87fa6b1baae98a810499415148a396b86a46fe0e25614"});
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
