(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d92ed7cbc3115e19.js","sha256":"d92ed7cbc3115e19b00dd118bf9bc23f3143646520159415e78def1f7b7529ad","count":2174,"publishedAt":"2026-11-11T17:13:50Z","state":"calendar-state.json","stateSha256":"d1dfc426c56b79c9c07a6f37bb3c879134fbef44b42eff895ee22f24c083917f","sourceState":"calendar-source-state.json","sourceStateSha256":"dfae01cc50cef38373df2305f1e195bf451d3c90a776880caa31c128ccb936b3"});
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
