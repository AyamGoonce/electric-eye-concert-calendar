(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.10b4b013cc3ecd65.js","sha256":"10b4b013cc3ecd65c0dcf4952aebba60a369bcf3f1f0217338d331749f9d0b30","count":2044,"publishedAt":"2026-08-29T00:11:42Z","state":"calendar-state.json","stateSha256":"fed185d272aac7131328ff9325fbdd17c92ff48a8fc1a4037fb5f605ec6f9e4d"});
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
