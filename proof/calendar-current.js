(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5c55bb964a9b8469.js","sha256":"5c55bb964a9b84692446ef0b34cd9fbb70b685842c1d99dc57ca8032edb583d2","count":2073,"publishedAt":"2026-10-19T18:29:04Z","state":"calendar-state.json","stateSha256":"29e5621a25e0dc1fb09a65c049f96f8f61782258c8bde1f07af97af93524d612","sourceState":"calendar-source-state.json","sourceStateSha256":"a2a3b01c5f638e853bf9dbd0eba395cc1f4d2eede30403b59f56892f5759db7f"});
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
