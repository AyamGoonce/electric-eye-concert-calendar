(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b2af4af393c87172.js","sha256":"b2af4af393c871728bd8ea8a5d08dde7ba07ce72cd21221abd4f5f6b1a74ef46","count":2053,"publishedAt":"2026-10-19T04:51:56Z","state":"calendar-state.json","stateSha256":"59bc6cf47c417966036ac45ca1f1aa3820d0dab52ba5d7957b02564ed571bd21","sourceState":"calendar-source-state.json","sourceStateSha256":"a6b363b041dbe734d473ec9d05da0f8be3e33e5ee01b2dda7d29c3babe3073ab"});
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
