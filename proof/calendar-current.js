(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.289ffdcd9cd96ceb.js","sha256":"289ffdcd9cd96ceb9d46116b63c53bd68ebbd11c2d0f6fd5fad76aff451be572","count":1712,"publishedAt":"2026-08-26T08:13:41Z","state":"calendar-state.json","stateSha256":"2085e167a8e0dd64494330f078128841481695b8abc9e760dd3c90cfb3677ac7"});
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
