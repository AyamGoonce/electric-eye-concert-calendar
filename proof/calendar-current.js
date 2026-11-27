(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f99f2553eda5b824.js","sha256":"f99f2553eda5b824f96a480f70ef6129cbeab05cbf9b85b70c2e803195ddfea9","count":2106,"publishedAt":"2026-11-27T11:32:10Z","state":"calendar-state.json","stateSha256":"2eca8554dee1759f9c0fe3a98636002bb3b6a731673a6bf56287df5bdd0bc8a0","sourceState":"calendar-source-state.json","sourceStateSha256":"0cdf8d35ff6db4863e4e21a8692a84c9fa32538a7fe40e6eae15ba3a7edb29ff"});
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
