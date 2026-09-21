(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a38146318caef254.js","sha256":"a38146318caef2543900c65613ce8ef0a092c28de76cf86fdd9073d1a1cfae3e","count":2137,"publishedAt":"2026-09-21T10:13:27Z","state":"calendar-state.json","stateSha256":"2e4fccad98548aebd66ebc8de00d9cba9b0c1fe64e094825297dfa45b0606c68"});
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
