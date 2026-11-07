(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.47aacc068282bf94.js","sha256":"47aacc068282bf941f9a067ee351836744e829d0274a6fd1556a31467ef53afa","count":2010,"publishedAt":"2026-11-07T06:09:37Z","state":"calendar-state.json","stateSha256":"b4c8d9e2b0fc93cec95cb37f75ee1752efce7c5958d93fa588b4a17a53b229e5","sourceState":"calendar-source-state.json","sourceStateSha256":"451bfbb763655d51b58244d5882ea6fc8b8f5b9b4b1379b7edbc709e8a23867d"});
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
