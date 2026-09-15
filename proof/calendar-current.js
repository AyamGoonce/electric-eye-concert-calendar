(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.fb2b77963c9813d5.js","sha256":"fb2b77963c9813d52c5113fee99520358721226d6e84c6766b0384a69a2e216f","count":2490,"publishedAt":"2026-09-15T17:08:03Z","state":"calendar-state.json","stateSha256":"bcdab6e3cec9f1e484a91123fd6a62f479348629e08c4769820c1aafe7c5b787"});
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
