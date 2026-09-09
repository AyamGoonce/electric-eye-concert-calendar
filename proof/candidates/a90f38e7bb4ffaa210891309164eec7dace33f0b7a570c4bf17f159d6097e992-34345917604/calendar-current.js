(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a90f38e7bb4ffaa2.js","sha256":"a90f38e7bb4ffaa210891309164eec7dace33f0b7a570c4bf17f159d6097e992","count":2501,"publishedAt":"2026-09-09T11:34:40Z","state":"calendar-state.json","stateSha256":"28bc06cdf36fe87f3be0453c86f4ee0eb5d2ebf0b26e61c7de67d6869ef93702"});
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
