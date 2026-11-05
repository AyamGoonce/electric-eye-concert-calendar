(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f5885f1517a45399.js","sha256":"f5885f1517a4539951a0c92aae4eb566d8b3d819c8ab07fecdceef115d972102","count":2041,"publishedAt":"2026-11-05T17:29:21Z","state":"calendar-state.json","stateSha256":"9e850663ee2b93508cf7a2418b0755acb5d7213b051719536597d68464b5df19","sourceState":"calendar-source-state.json","sourceStateSha256":"c863c57764d51a141364d229fd1fbfb8f5563a307d5767011653147dad8fcb2c"});
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
