(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3d05e809dc5fc25d.js","sha256":"3d05e809dc5fc25d1ccce96deb3200b81c594a98b7b6c77021069afccb6af818","count":2080,"publishedAt":"2026-10-20T15:31:57Z","state":"calendar-state.json","stateSha256":"89d8965b56680fc1e93a78044c7c3291a91c9b1ffc0f2161fcfe5a342e2d31dc","sourceState":"calendar-source-state.json","sourceStateSha256":"263a43fc5410e51019bd1d69e37b526edf7a3db2024ebe331a971b23eb98e1ba"});
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
