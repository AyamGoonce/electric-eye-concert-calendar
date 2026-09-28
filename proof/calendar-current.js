(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.293f26a8839b07b1.js","sha256":"293f26a8839b07b147fba03f6820e7ddb92da37d15e473f8ce3a04e886a29c61","count":2078,"publishedAt":"2026-09-28T21:15:58Z","state":"calendar-state.json","stateSha256":"58dff3961ed6b96472f99c5e29c44c56b30186e2278b96422eca0514aad2514a","sourceState":"calendar-source-state.json","sourceStateSha256":"0b96578e1047f211ca9bd4f0a71bdac39bf209887b92e187e7922ff5ea6a1b68"});
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
