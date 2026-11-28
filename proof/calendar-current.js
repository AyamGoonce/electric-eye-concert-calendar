(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cbecba1a56b9ce20.js","sha256":"cbecba1a56b9ce20c787bbe7dd6ad3bb91a4211b3331ae3a53d8af695a8e6666","count":2098,"publishedAt":"2026-11-28T07:58:00Z","state":"calendar-state.json","stateSha256":"4d7849bb55fc3ea1e7f503aead1c2afac6e913269a8a8c48befb198c2e5663ad","sourceState":"calendar-source-state.json","sourceStateSha256":"7f1e4fc0e46c589e46f0159b0246d99147744f86ed0fca7ac9e4cb5d8749f29f"});
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
