(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5eb36fd90da40c44.js","sha256":"5eb36fd90da40c4463a7bc869fea8af09bc3a07cf12757507b57676ce36bfd16","count":2207,"publishedAt":"2026-09-18T21:01:21Z","state":"calendar-state.json","stateSha256":"71d847e8b34cc5eeeb76cb879d69d57fffba772d015a941bd54995df12e43716"});
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
